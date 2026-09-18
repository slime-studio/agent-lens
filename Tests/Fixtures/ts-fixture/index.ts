function greet(name: string): string {
  return "hello " + name;
}

const x: number = "this is not a number";  // error: Type 'string' is not assignable to type 'number'.

console.log(greet("world"));
