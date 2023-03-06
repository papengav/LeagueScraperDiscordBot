import leagueScraper as ls
import bot
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def main():
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url = "https://leaguescrapervault.vault.azure.net/", credential = credential)
    
    
    apiKey = secret_client.get_secret("RIOT-API-KEY")
    devId = secret_client.get_secret("DEV-ID")
    botToken = secret_client.get_secret("BOT-TOKEN")

    ls.init(apiKey.value)
    bot.init(devId.value, botToken.value)

def closeBot():
    bot.client.close()

if __name__ == "__main__":
    main()