
class StringReply(object):
	def __init__(self, message):
		self.message=message
    
	def __call__(self, orig_message, match): 
		msg = self.message.format(orig_message)
		return msg
    
