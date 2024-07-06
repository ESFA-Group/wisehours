const d1 = [
    {id: 0, name: 'steakd', price: 250},
    {id: 1, name: 'kebab', price: 100},
    {id: 2, name: 'chicken', price: 80},
    {id: 3, name: 'coca', price: 10}
];

const d2 = [
    {id: 0, name: 'steakd', price: 250},
    {id: 1, name: 'kebab', price: 100},
    {id: 2, name: 'chicken', price: 80},
    {id: 3, name: 'coca', price: 10}
];

console.log(JSON.stringify(d1) === JSON.stringify(d2)); // Expected output: true
