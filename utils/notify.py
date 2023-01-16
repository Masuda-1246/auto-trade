import requests
import configparser
conf = configparser.ConfigParser()
conf.read("config.ini")


def pprint(message):
  s = ''
  if isinstance(message, dict):
    for k, v in message.items():
      s += f'{k}: {v} \n'
    message = s
  return "\n" + message

def send_message_to_line(message):
  token = conf["line"]["token"]
  header = {
    'Authorization': f'Bearer {token}'
  }
  data = {"message":pprint(message)}
  requests.post("https://notify-api.line.me/api/notify", headers=header, data=data)
