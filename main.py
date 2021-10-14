import requests
import re
import logging, time
import sys, pickle
from pandas import DataFrame



print("""
 =============== RTechS ==============
 =      Rusman Tobyakta Siregar      =
 =        IG: @rusman_toby           =
 =       rusmants.public@pm.me       =
 =====================================
""")

logging.basicConfig(format='[%(asctime)s] %(levelname)-8s: %(message)s',datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO, handlers=[logging.FileHandler('./log.log'), logging.StreamHandler(sys.stdout)])
#logging.basicConfig(format='[%(asctime)s] %(levelname)-8s: %(message)s',datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO, handlers=[logging.FileHandler('./log.log')])

head = {'User-Agent':"Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0","Connection":"keep-alive"}
prc_jumlah_parameters = 25


t_awal = None
t_akhir = None

def title_to_url(title):
	i = re.sub(r"\[(.*?)\]", "olx",title.lower()).split()
	d = ""
	for j in i:
		p = ''.join(re.findall("([a-z]|[\d])", j))
		if p != '':
			d += p+"-"
	return d

class Main:
	def __init__(self):
		self.listDaerah = {}
		self.data_raw = []
		self.data_filter = []
		self.parameters_keys = []
		self.requests = requests.Session()
		self.head = {'User-Agent':"Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0"}
		self.table_title = ['Id', 'Judul', 'Waktu', 'Deskripsi', 'Harga', 'Provinsi', 'Kota/Kab', 'Lokasi', 'Handphone', 'Penjual', 'Url']
		self.cache_info_seller = {}
		self.webpage_load = 2

	def save_to_pickle(self, lok, data):
		try:
			with open(lok, 'wb') as tulis:
				pickle.dump(data, tulis)
			print(f'[SAVED] Pickle => {lok}')
			return True
		except:
			return False

	def save_to_csv(self, lok):
		try:
			df = DataFrame(self.data_filter, columns=self.table_title)
			df.to_csv(lok, index=False)
			return {'status':True, 'location':lok}
		except:
			logging.exception('Error save to csv')
			return {'status':False}

	def login(self, US, PW):
		PW = PW.strip('\n')

		try:
			loginUS = self.requests.post('https://www.olx.co.id/api/auth/authenticate', headers=self.head, json={"grantType":"email","email":US,"language":"id"})

			bear = 'Bearer '+loginUS.json()['token']
			headPW = {'User-Agent':"Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0", 'Authorization':bear}
			loginPW = self.requests.post('https://www.olx.co.id/api/auth/authenticate/login', headers=headPW, json={"grantType":"password","password":PW,"email":US,"language":"id","metadata":{"deviceInfo":""}})
			reqME = self.requests.get('https://www.olx.co.id/api/users/me', headers=self.head)

			if 'error' in reqME.json():
				logging.exception(reqME.content)
				return False
			else:
				return True
		except:
			logging.exception("Error login")
			return False

	def search_location(self):
		lokasi = input('Daerah : ')
		try:
			urlLoc = f'https://www.olx.co.id/api/locations/autocomplete?input={lokasi}&limit=5'
			reqLoc = self.requests.get(urlLoc, headers=head)
			if len(reqLoc.json()['data']['suggestions']) > 0:
				for num, i in enumerate(reqLoc.json()['data']['suggestions']):
					self.listDaerah[num+1] = [i['id'], i['name'], i['type']]
					print(f"{num+1}. {i['name']} ({i['type']})")

				pilihanDaerah = int(input('Pilih nomor lokasi : '))
				self.idDaerah = 1
				if type(pilihanDaerah) == int and pilihanDaerah in self.listDaerah:
					#print(self.listDaerah[pilihanDaerah])
					self.idDaerah = self.listDaerah[pilihanDaerah][0]
				
				print(f'[SUCCES] Lokasi : {self.listDaerah[1][1]}')
				self.lokasi = self.listDaerah[1][1]
				return True
			else:
				return False
		except:
			logging.exception("Error search_location")

	def max_data(self):
		print("\nSemakin banyak maka semakin lama, jumlah disarankan dari kelipatan 20")
		try:
			max_data = int(input('Maximal Data : '))
			if max_data <= 20:
				self.webpage_load = 0
			
			h = max_data/20
			if h > int(h):
				h = int(h)+1

			self.webpage_load = h
		except:
			self.webpage_load = 0


	def search_query(self):
		q = input('\nKata Kunci : ')
		self.max_data()

		jumlah_search_query = 20*self.webpage_load
		num = 0

		for o in range(int(self.webpage_load)):
			er = False
			try:
				time.sleep(0.3)
				urlProduk = f'https://www.olx.co.id/api/relevance/v2/search?facet_limit=200&location={self.idDaerah}&location_facet_limit=30&platform=web-desktop&query={q}&spellcheck=true&page={o}'
				
				try:
					reqProduk = self.requests.get(urlProduk, headers=head,timeout=3)
					er = False
					if len(reqProduk.json()['data']) == 0 or 'data' not in reqProduk.json():
						er = True
					if reqProduk.status_code != 200:
						er = True
				except:
					er = True


				if er == False :
					for i in reqProduk.json()['data']:
						num += 1
						self.data_raw.append(i)
						n = num+1

						prc = (n/jumlah_search_query)*100
						print('Search ['+'#'*int(prc/2),' '*int((100-prc)/2),']'+f' {int(prc)}%','\r', end='')
						
				else:

					prc = 100
					print('Search ['+'#'*int(prc/2),' '*int((100-prc)/2),']'+f' {int(prc)}%','\r', end='')
					break

					
				if len(self.data_raw) == 0:
					print('Tidak ditemukan')
					break
			except:
				logging.exception("Error search_query")
		self.query = q

		if len(self.data_raw) > 0:
			print('[SUCCES] Search Data')
			return True
		else:
			print('[FAILED] Data not found')
			return False

	def get_user_detail(self, idUser):
		try:

			if idUser in self.cache_info_seller:
				detail = [self.cache_info_seller[idUser][0], self.cache_info_seller[idUser][1]]
			else:
				req_cekUser = self.requests.get(f'https://www.olx.co.id/api/users/{idUser}', headers=self.head)
				req_cekUser = req_cekUser.json()['data']
				detail = [req_cekUser['phone'], req_cekUser['name']]

				self.cache_info_seller[idUser] = detail

			return detail
		except:
			logging.exception('Error get detail penjual')
			return [0,'']

	def filter_parameters(self, jumlah_data_raw):
		count_parameters_keys = {}
		for i in self.data_raw:
			for par in i['parameters']:
				if par['key_name'] not in count_parameters_keys:
					count_parameters_keys[par['key_name']] = 1
				else:
					count_parameters_keys[par['key_name']] += 1

		min_jumlah_parameters = (prc_jumlah_parameters/100)*jumlah_data_raw

		for pr in count_parameters_keys:
			if count_parameters_keys[pr] >= min_jumlah_parameters:
				self.table_title.append(pr)
				self.parameters_keys.append(pr)


	def filter_data(self):
		jumlah_data_raw = len(self.data_raw)
		
		self.filter_parameters(jumlah_data_raw)

		for num,i in enumerate(self.data_raw):
			user_detail = self.get_user_detail(i['user_id'])

			lokasi_barang = ['','','']
			harga = None
			parameters = []

			for key in self.parameters_keys:
				tmp_parameters = {}

				for par in i['parameters']:
					try:
						if par['type'] == 'single':
							tmp_parameters[par['key_name']] = par['formatted_value']
						elif par['type'] == 'multi':

							tmp_value = []
							for vl in par['values']:
								tmp_value.append(vl['value'])
							tmp_value = ', '.join(tmp_value)

							tmp_parameters[par['key_name']] = tmp_value
					except:
						print(par)
						exit()

				h = ''
				if key in tmp_parameters:
					h = tmp_parameters[key]

				parameters.append(h)

			if 'locations_resolved' in i:

				try:
					keyy = i['locations_resolved'].keys
					#print(keyy)

					if 'ADMIN_LEVEL_1_name' in i['locations_resolved']:
						lokasi_barang[0] = i['locations_resolved']['ADMIN_LEVEL_1_name']

					if 'ADMIN_LEVEL_3_name' in i['locations_resolved']:
						lokasi_barang[1] = i['locations_resolved']['ADMIN_LEVEL_3_name']

					if 'SUBLOCALITY_LEVEL_1_name' in i['locations_resolved']:
						lokasi_barang[2] = i['locations_resolved']['SUBLOCALITY_LEVEL_1_name']
				except:
					print(i['locations_resolved'])

			if i['price'] != None:
				harga = i['price']['value']['raw']


			urlBarang = f"https://www.olx.co.id/item/{title_to_url(i['title'])}iid-{i['id']}"
			try:
				tmp_data_filter = [i['id'], i['title'], i['created_at'], i['description'],  harga, lokasi_barang[0],lokasi_barang[1],lokasi_barang[2], user_detail[0], user_detail[1], urlBarang]
				for pr in parameters:
					tmp_data_filter.append(pr)

				self.data_filter.append(tmp_data_filter)
			except:
				logging.exception("Gagal memfilter data")

			n = num+1

			prc = (n/jumlah_data_raw)*100
			print('Filter ['+'#'*int(prc/2),' '*int((100-prc)/2),']'+f' {int(prc)}%','\r', end='')

		print('[SUCCES] Filter Data')

		self.save_to_pickle(f"hasil/pickle/{self.lokasi}-{self.query}.pickle", {'title':self.table_title, 'data':self.data_filter})

		lok = f"hasil/csv/{self.lokasi}-{self.query}.csv"
		self.save_to_csv(lok)
		print(f'[SAVED] CSV => {lok}')
		print(f'[INFO] Total => {len(self.data_filter)}')


if __name__ == '__main__':
	main = Main()
	try:
		with open('login.txt') as baca:
			pecah = baca.read().split(':')
			US = pecah[0]
			PW = pecah[1]
	except:
		US = input("Email: ")
		PW = input("Password: ")
	print('[Wait] Proses Login ..\r', end='')
	go_login = main.login(US,PW)
	if go_login: 
		print('[SUCCES] Login Success !!')
		go_search_location = main.search_location()
		if go_search_location:
			t_awal = time.time()
			go_search_query = main.search_query()
			if go_search_query:
				
				main.filter_data()
				
				t_akhir = time.time()
				print('[FINISH] Duration: ',t_akhir-t_awal, ' Second')
				input('')
			else:
				print('[FAILED] Kata kunci tidak ditemukan')
		else:
			print('[FAILED] Tidak ada lokasi yang cocok')
	else:
		print('[FAILED] Login Failed !!')
