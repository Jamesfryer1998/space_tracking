import * as THREE from 'three';


export default class DataLoader {
    constructor(fileName) {
      this.fileName = fileName;
    }
  

    fetchTest() {
      console.log('Fetching JSON: ')
      fetch(this.fileName) 
      .then(Response => Response.json())
      .then(data => {
          console.log(data);
        // or whatever you wanna do with the data
      });

    }
  }

