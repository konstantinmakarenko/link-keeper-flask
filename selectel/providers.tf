terraform {
  required_version = ">= 1.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 2.1.0"
    }
    selectel = {
      source  = "selectel/selectel"
      version = "~> 7.1.0"
    }
  }
}

provider "selectel" {
  domain_name = var.account_id
  username    = var.service_user
  password    = var.service_password
  auth_url    = "https://cloud.api.selcloud.ru/identity/v3"
  region      = var.region
  auth_region = var.region
}

provider "openstack" {
  auth_url    = "https://cloud.api.selcloud.ru/identity/v3"
  domain_name = var.account_id
  tenant_id   = var.project_id
  user_name   = var.service_user
  password    = var.service_password
  region      = var.region
}