// webpack.config.js
const path = require('path');

module.exports = {
  target: ['web', 'es5'],
  entry: './esfa_persian_holidays.js',
  mode: 'production',
  output: {
    filename: 'esfa_persian_holidays.min.js',
    path: path.resolve('./build'),
    library: {
      name: 'EsfaPersianHolidays',
      type: 'umd',
      umdNamedDefine: false
    }
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
        },
      },
    ],
  },
};
