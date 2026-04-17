resource "azurerm_storage_account" "storage" {
  name                     = "stmanufacturingvault2026"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  public_network_access_enabled = false
}

resource "azurerm_storage_container" "vault" {
  name                  = "manufacturing-vault"
  storage_account_id    = azurerm_storage_account.storage.id
  container_access_type = "private"
}

resource "azurerm_role_assignment" "storage_mes_access" {
  scope                = azurerm_storage_account.storage.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_user_assigned_identity.mes_identity.principal_id
}
