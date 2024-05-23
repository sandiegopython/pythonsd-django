const webpack = require('webpack');
const path = require('path');

const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');

const INPUT_DIR = path.resolve(__dirname, './assets/src');
const OUTPUT_DIR = path.resolve(__dirname, './assets/dist');

module.exports = {
  entry: path.resolve(INPUT_DIR, 'index.js'),
  output: {
    path: OUTPUT_DIR,
    filename: 'bundle.js'
  },
  module: {
    rules: [{
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
    }, {
      // the file-loader emits files directly to OUTPUT_DIR/fonts
      test: /\.(woff(2)?|ttf|eot)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
      type: 'asset/resource',
    }, {
      // Image loader
      // the file-loader emits files directly to OUTPUT_DIR/img
      test: /\.(png|gif|jpg|jpeg|svg)$/,
      type: 'asset/resource',
    }]
  },
  optimization: {
    minimizer: [
      // https://webpack.js.org/plugins/terser-webpack-plugin/
      new TerserPlugin(),

      // https://webpack.js.org/plugins/css-minimizer-webpack-plugin/
      new CssMinimizerPlugin(),
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      // Options similar to the same options in webpackOptions.output
      filename: '[name].css',
      chunkFilename: '[id].css'
    }),

    // Makes jQuery (required for bootstrap4) available to other JS includes
    // https://webpack.js.org/plugins/provide-plugin/
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      'window.jQuery': 'jquery'
    }),
  ]
};
