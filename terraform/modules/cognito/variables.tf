variable "user_pool_name" {}
variable "app_client_name" {}
variable "callback_urls" {
  type = list(string)
}
variable "logout_urls" {
  type = list(string)
}
variable "region" {}
