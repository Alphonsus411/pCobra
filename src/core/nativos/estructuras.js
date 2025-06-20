export class Pila {
    constructor() {
        this._datos = [];
    }
    apilar(v) {
        this._datos.push(v);
    }
    desapilar() {
        return this._datos.pop();
    }
}

export class Cola {
    constructor() {
        this._datos = [];
    }
    encolar(v) {
        this._datos.push(v);
    }
    desencolar() {
        return this._datos.shift();
    }
}
