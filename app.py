from flask import Flask, render_template, request, Response

# NLP
import re
import matplotlib.pyplot as plt
import nltk
from googletrans import Translator
from string import punctuation, digits
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('vader_lexicon')

app = Flask(__name__)

sentiment = 'Sentimiento'
graph = 'graph.png'
input_user = ''
response = Response()

@app.after_request
def cache_bug(r):
    r.headers["Cache-Control"] = "no-store"
    return r


@app.route('/')
def hello_world():
    return render_template('index.html', sentiment=sentiment, graph=graph)


@app.route("/analyze", methods=['POST'])
def analyze():
	cache_bug(response)
	input_text = request.form['text_box']
	if input_text == '':
		input_text = open('text.txt', encoding='utf-8').read()
	sentiment_found = work(input_text)
	sentiment = sentiment_found
	return render_template('index.html', input_user = input_text, sentiment=sentiment_found, graph=graph)


def work(input_texto):
	# Entrada del usuario
	translated_text = translate_to_spanish(input_texto)

	cleaned_text = try_input(translated_text)

	# Dividir el texto en palabras
	tokenized_words = word_tokenize(cleaned_text, 'english')

	# Traer los stops words de nltk
	stop_words = stopwords.words('english')

	# Eliminar los stop words de las palabras separadas (tokenized_words)
	final_words = []
	for word in tokenized_words:
		if word not in stop_words:
			final_words.append(word)

	# Expresion regular para tratar el archivo de emociones y separarlo en clave valor
	# Palabra comun : emocion que expresa
	reg_express = re.compile('[^(:|\w)]')

	emotions_list = []
	with open('emotions.txt', 'r') as emotions_file:
		for line in emotions_file:
			clear_line = reg_express.sub('', line).strip()
			word, emotion = clear_line.split(':')

			if word in final_words:
				for times in range(0, final_words.count(word)):
					emotions_list.append(emotion)

	# Contar la cantidad de veces que esta un sentimiento
	count = Counter(emotions_list)
	final = {k: v for k, v in sorted(count.items(), key=lambda item: item[1])}
	sentiment_found = list(final.keys())[-1]

	# Realizar la grafica de los sentimientos y guardarla en un archivo de imagen
	fig1, ax1 = plt.subplots()
	ax1.pie([float(v) for v in count.values()], labels=[k for k in count], autopct='%1.1f%%', startangle=90,
			wedgeprops={'alpha': 0.9})
	ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
	fig1.set_facecolor('#3782FF')
	plt.savefig('static/graph.png')

	return sentiment_found


def translate_to_spanish(input_texto):
	translator = Translator()
	text = input_texto
	return translator.translate(text, dest='en').text


def try_input(translated_text):
	# Convirtiendo a minuscula la entrada del usuario
	lower_case_text = translated_text.lower()
	# Eliminando caracteres especiales
	return lower_case_text.translate(str.maketrans('', '', punctuation))


@app.route("/clear")
def clear_input():
    input_user = ''
    return render_template('index.html', input_user = input_user, sentiment=sentiment, graph=graph)

if __name__ == '__main__':
	app.run()