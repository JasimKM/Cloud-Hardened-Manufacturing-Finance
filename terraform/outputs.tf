output "app_gateway_public_ip" {
  value = azurerm_public_ip.pip.ip_address
}

output "mes_vm_private_ip" {
  value = azurerm_linux_virtual_machine.mes_vm.private_ip_address
}

output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}
