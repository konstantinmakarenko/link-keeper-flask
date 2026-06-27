output "vm_public_ip" {
  description = "Публичный IP-адрес ВМ"
  value       = selectel_vpc_floatingip_v2.vm_floatingip.floating_ip_address
}

output "vm_private_ip" {
  description = "Приватный IP-адрес ВМ"
  value       = openstack_compute_instance_v2.vm.network[0].fixed_ip_v4
}