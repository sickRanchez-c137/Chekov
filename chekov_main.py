import os
import sys
import keras
import os.path
import numpy as np
from keras.utils import np_utils
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, LSTM
from keras.callbacks import ModelCheckpoint

class Chekov:
	def __init__(self,model=""):
		self.text_read = ""
		self.model_name = model

	def read_file(self,file_name):
		if not os.path.exists(file_name):
			print(f"E: file {file_name} not found")
			return ""
		text_read = open(file_name).read().lower()
		return text_read

	def process_file_text(self,folder_name,num_stories_to_learn=1):
		self.my_text_corpus = ""
		for i in range(1,num_stories_to_learn+1):
			file_name = os.path.join(folder_name,f"{i}.txt")
			if not os.path.exists(file_name):
				print(f"E: file {file_name} not found")
				continue
			self.my_text_corpus += self.read_file(file_name)
		
		self.n_chars = len(self.my_text_corpus)
		print(f":I .. Total characters read = {self.n_chars}")

		# list of unique chars in the file
		self.chars = sorted(list(set(self.my_text_corpus)))
		self.n_vocab = len(self.chars)
		print(f"Ï: .. Unique Characters are {self.n_vocab}")
		print(self.chars)

		# create a dict to get index of each char 
		self.char_index = dict((c,i) for i,c in enumerate(self.chars))
		self.index_char = dict((i,c) for i,c in enumerate(self.chars))

	def prepare_data(self,input_seq_length = 100):
		self.in_sequences = []
		self.outputs = []
		self.input_seq_length = input_seq_length

		for i in range(0,self.n_chars-input_seq_length,1):
			in_sequences_temp = self.my_text_corpus[i:i+input_seq_length]
			outputs_temp = self.my_text_corpus[i+input_seq_length]	# this is supposed to be output for above sequence
			
			self.in_sequences.append([self.char_index[char] for char in in_sequences_temp])
			self.outputs.append(self.char_index[outputs_temp])
		self.total_sequences = len(self.in_sequences)
		print(f"I: ..We have total of {self.total_sequences} each of length {input_seq_length} chars")

		self.in_sequences = np.reshape(self.in_sequences,(self.total_sequences,input_seq_length,1))
		self.in_sequences = self.in_sequences/float(self.n_vocab)
		self.outputs = np_utils.to_categorical(self.outputs)
		return

	def create_model(self):
		self.model = Sequential()
		self.model.add(LSTM(256,input_shape=(self.in_sequences.shape[1],self.in_sequences.shape[2]),return_sequences=True))
		self.model.add(Dropout(0.2))
		self.model.add(LSTM(256))
		self.model.add(Dropout(0.2))
		self.model.add(Dense(self.outputs.shape[1],activation='softmax'))

		if self.model_name=="":
			self.model.compile(loss='categorical_crossentropy',optimizer='adam')
			check_point_save_file = "weight_improvement-{epoch:02d}-{loss:.4f}.hdf5"
			checkpoint = ModelCheckpoint(check_point_save_file,monitor='loss',verbose=1,save_best_only=True,mode='min')
			callbacks_list=[checkpoint]
			self.model.fit(self.in_sequences,self.outputs,epochs=20,batch_size=128,callbacks=callbacks_list)
		else:
			self.model.load_weights(self.model_name)
			self.model.compile(loss='categorical_crossentropy',optimizer='adam')		

	def process(self):
		in_folder_name = 'my_stories'
		num_stories_to_learn = 1
		self.process_file_text(in_folder_name,num_stories_to_learn)
		self.prepare_data()

	def operate(self):
		if self.model_name=="":
			self.process()
		else:
			if os.path.exists(self.model_name):
				self.process()
			else:
				print(f"I: .. Could not find specified model. Training again")
				self.model_name=""
				self.process()
		self.create_model()

	def write_story(self,output_length = 10000):
		
		my_start = input("Please Enter Some text as paragraph that will start the story.\n")
		print(f"I: .. you entered string of length {len(my_start)}")
		sentence = my_start.rjust(self.input_seq_length)[:self.input_seq_length].lower()
		print(f"I: .. string made of length {len(sentence)}")

		generated_text = ""
		# convert the characters to their index
		sentence_int = np.asarray([self.char_index[my_char] for my_char in sentence])

		for i in range(output_length):
			x =  np.reshape(sentence_int,(1,self.input_seq_length,1))
			x = x/float(self.n_vocab)

			preds = self.model.predict(x,verbose=0)
			index = np.argmax(preds)
			result = self.index_char[index]
			generated_text+=result
			sentence_int = np.append(sentence_int,index)
			sentence_int = sentence_int[1:]

		output_file = "chekov_gen.txt"
		print(f"I: .. writing to output file {output_file}")
		with open(output_file,'wb') as o_file:
			outfile.write(generated_text.encode('ascii','ignore'))
		print(f"I: .. output file write completed")

my_obj = Chekov()
my_obj.operate()
