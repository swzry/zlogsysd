
class PageCounter():
	def __init__(self,dbo,ipp):
		self.items_per_page = ipp
		self.num_of_items = dbo.count()
		self.remain = self.num_of_items % ipp
		pn = (ct - remain) / ipp
		if self.remain > 0:
			self.num_of_pages = pn + 1
		else:
			self.num_of_pages = pn
		self.current_page = 1
	def setCurrentPage(self,current):
		if current > 0 and current <= self.num_of_pages:
			self.current_page = current
			if current > 1:
				self.previous_page = current - 1
				self.has_previous = True
			else:
				self.previous_page = 1
				self.has_previous = False
			if current == self.num_of_pages:
				self.next_page = current
				self.has_next = False
			else:
				self.next_page = current + 1
				self.has_next = True
		else:
			self.current_page = 1
			self.previous_page = 1
			self.has_previous = False
			if self.num_of_pages > 1:
				self.next_page = 2
				self.has_next = True
			else:
				self.next_page = 1
				self.has_next = False
