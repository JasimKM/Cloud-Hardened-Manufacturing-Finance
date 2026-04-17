terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "dbc52263-497d-416f-bf1f-e910a494af09"
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

# --- Network Layer (Purdue Reference Model) ---

resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-manufacturing-hub"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "dmz" {
  name                 = "snet-dmz-level4"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "mes" {
  name                 = "snet-mes-level3"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_subnet" "scada" {
  name                 = "snet-scada-level2"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.3.0/24"]
}

resource "azurerm_subnet" "controller" {
  name                 = "snet-controller-level0-1"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.4.0/24"]
}

# --- WAF Policy (OWASP 3.2 + Custom Rules) ---

resource "azurerm_web_application_firewall_policy" "waf_policy" {
  name                = "waf-manufacturing-policy"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.2"
    }
  }

  policy_settings {
    enabled = true
    mode    = "Prevention"
  }

  custom_rules {
    name      = "BlockDangerousFileTypes"
    priority  = 1
    rule_type = "MatchRule"
    action    = "Block"

    match_conditions {
      match_variables {
        variable_name = "RequestHeaders"
        selector     = "Content-Disposition"
      }
      operator           = "Contains"
      negation_condition = false
      match_values       = [".exe", ".dll", ".bat", ".sh"]
    }
  }
}

# --- Application Gateway (Level 4 DMZ) ---

resource "azurerm_public_ip" "pip" {
  name                = "pip-manufacturing-vault"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_application_gateway" "app_gateway" {
  name                = "appgw-manufacturing-vault"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 1
  }

  gateway_ip_configuration {
    name      = "my-gateway-ip-configuration"
    subnet_id = azurerm_subnet.dmz.id
  }

  frontend_port {
    name = "http-port"
    port = 80
  }

  frontend_ip_configuration {
    name                 = "my-frontend-ip-configuration"
    public_ip_address_id = azurerm_public_ip.pip.id
  }

  backend_address_pool {
    name = "mes-backend-pool"
  }

  backend_http_settings {
    name                  = "http-setting"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 60
  }

  http_listener {
    name                           = "http-listener"
    frontend_ip_configuration_name = "my-frontend-ip-configuration"
    frontend_port_name             = "http-port"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "rule1"
    rule_type                  = "Basic"
    http_listener_name         = "http-listener"
    backend_address_pool_name  = "mes-backend-pool"
    backend_http_settings_name = "http-setting"
    priority                   = 1
  }

  firewall_policy_id = azurerm_web_application_firewall_policy.waf_policy.id
}

# --- Compute Layer (Level 3 MES VM) ---

resource "azurerm_user_assigned_identity" "mes_identity" {
  name                = "id-mes-app"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

resource "azurerm_network_interface" "mes_nic" {
  name                = "nic-mes-app"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.mes.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_network_interface_application_gateway_backend_address_pool_association" "mes_nic_assoc" {
  network_interface_id    = azurerm_network_interface.mes_nic.id
  ip_configuration_name   = "internal"
  backend_address_pool_id = tolist(azurerm_application_gateway.app_gateway.backend_address_pool).0.id
}

resource "azurerm_linux_virtual_machine" "mes_vm" {
  name                = "vm-mes-app"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  size                = "Standard_B2s_v2"
  admin_username      = "azureuser"

  network_interface_ids = [azurerm_network_interface.mes_nic.id]

  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.mes_identity.id]
  }
}
