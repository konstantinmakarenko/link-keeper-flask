variable "account_id" {
  description = "Номер аккаунта Selectel"
  type        = string
  sensitive   = true
}

variable "service_user" {
  description = "Имя сервисного пользователя"
  type        = string
  sensitive   = true
}

variable "service_password" {
  description = "Пароль сервисного пользователя"
  type        = string
  sensitive   = true
}

variable "project_id" {
  description = "ID проекта в Selectel"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "Регион Selectel"
  type        = string
  default     = "ru-9"
}

variable "public_ssh_key" {
  description = "Публичный SSH-ключ"
  type        = string
  sensitive   = true
}