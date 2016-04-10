
class StringReply(object):
  def __init__(self, message):
    self.message=message
    
  def __call__(self, orig_message): 
        msg = self.message.format(orig_message)
        yield from client.send_message(orig_message.channel, msg)
    