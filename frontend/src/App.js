import React from 'react'
import './App.css'
import Result from './Result.js'
import Dropzone from 'react-dropzone'


class App extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      image: null,
      uploading: false,
      response: null
    }

    this.handleFiles = this.handleFiles.bind(this)
  }

  async handleFiles(files) {
    this.setState({
      uploading: true,
      image: URL.createObjectURL(files[0]),
      response: null
    })

    console.log(files)
    new Promise((resolve, reject) => {
      const req = new XMLHttpRequest()

      const formData = new FormData()
      const file = files[0]
      formData.append("image", file, file.name)

      req.onload = function() {
        resolve(req.response)
      }

      req.open("POST", "http://localhost/faces")
      req.send(formData)
    }).then((response) => {
      this.setState({
        uploading: false,
        response: JSON.parse(response),
      })
    })
  }

  render() {
      return (
        <div className='App'>
          <Dropzone onDrop={this.handleFiles}>
            {({getRootProps, getInputProps}) => (
              <section>
                <div {...getRootProps({className: 'dropzone'})}>
                  <input {...getInputProps()} />
                  <p>Drag 'n' drop an image here, or click to select a file</p>
                </div>
              </section>
            )}
          </Dropzone>
          <br />
          <Result image={this.state.image} response={this.state.response} />
          
        </div>
      );
  }
}

export default App;
