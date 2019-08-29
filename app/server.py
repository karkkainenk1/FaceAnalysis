from aiohttp import web
import tempfile
import predictor
import logging
import asyncio
import argparse
import dlib


routes = web.RouteTableDef()
PORT = -1


@routes.post('/predict')
async def process_image(request):
	data = await request.post()

	image = data['image']
	image_file = image.file
	data = image_file.read()

	with tempfile.NamedTemporaryFile() as tmpfile:
		tmpfile.write(data)
		predictions = predictor.load_and_predict(tmpfile.name)

	return web.json_response({"faces": predictions})


@routes.get('/health')
async def process_image(request):
	return web.json_response({"health": "ok"})


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--port')
	args = parser.parse_args()

	logging.basicConfig(level=logging.DEBUG)

	app = web.Application(client_max_size=10000000)
	app.add_routes(routes)

	logging.info("dlib uses cuda {}".format(dlib.DLIB_USE_CUDA))

	logging.info("Loading model...")
	predictor.init()
	logging.info("Model loaded")

	global PORT
	PORT = args.port

	web.run_app(app, port=PORT)


if __name__ == '__main__':
	main()
	