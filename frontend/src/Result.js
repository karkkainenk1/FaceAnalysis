import React from 'react';
import Spinner from 'react-spinkit'

class Result extends React.Component {
	canvasPadding = 50
	rectanglePadding = 15

	calculateImageRect(img, maxSize) {
		var width = maxSize
    	var height = maxSize
    	var top = 0
    	var left = 0
    	if (img.width < img.height) {
    		width = width * (img.width/img.height)
    	} else {
    		height = height * (img.height/img.width)
    	}

    	if (width < height) {
    		// Center image horizontally
    		left = (maxSize-width) / 2
    	} else {
    		// Center image vertically
    		top = (maxSize-height) / 2
    	}
    	return {top, left, width, height}
	}

	componentDidUpdate() {
	    const canvas = this.refs.canvas
		if (canvas == null) {
			return
		}

	    const ctx = canvas.getContext("2d")
	    const img = this.refs.image

	    img.onload = () => {
	    	ctx.clearRect(0, 0, canvas.width, canvas.height)

	    	const {top, left, width, height} = this.calculateImageRect(img, canvas.width - this.canvasPadding*2)
	    	this.imgTop = top + this.canvasPadding
	    	this.imgLeft = left + this.canvasPadding
	    	this.imgWidth = width
	    	this.imgHeight = height

	    	ctx.drawImage(img, this.imgLeft, this.imgTop, this.imgWidth, this.imgHeight)
	    }

	    if (this.props.response != null) {
	    	this.props.response.faces.forEach((face) => {
	    		let rect = face.rectangle
	    		let top = rect.top*this.imgHeight - this.rectanglePadding + this.imgTop
	    		let left = rect.left*this.imgWidth - this.rectanglePadding + this.imgLeft
	    		let width = rect.width*this.imgWidth + this.rectanglePadding*2
	    		let height = rect.height*this.imgHeight + this.rectanglePadding*2

	    		ctx.beginPath()
		      	ctx.fillStyle = "#FFF"
		      	ctx.strokeStyle = "#FFF"
		      	ctx.lineWidth = 3
		     	ctx.rect(left, top, width, height)
		      	ctx.stroke()

		      	let attrs = face.attributes
		      	let text = attrs.gender + ", " + attrs.age + ", " + attrs.race
		      	let textSize = ctx.measureText(text)

		      	let textTop = top+height
		      	let textLeft = left - (textSize.width-width)/2

		      	ctx.fillRect(textLeft-4, textTop, textSize.width+8, 20)
		      	ctx.fillStyle = "#000"
		      	ctx.fillText(text, textLeft, textTop+15)

		      	})
	    }
	  }

	render() {
		return (
			<div>
				<br />
				<canvas ref="canvas" width={800} height={800}></canvas>
				{
					(this.props.image!=null && this.props.response==null) ? 
					(
						<div className="loader">
							<Spinner fadeIn='quarter' name='ball-spin-fade-loader' color='steelblue' />
						</div>
					) : null
				}
				
				<img src={this.props.image} ref="image" className="hidden" />
			</div>
		);
	}
}


export default Result;