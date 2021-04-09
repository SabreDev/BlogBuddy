const mongoose = require('mongoose');

const articles = new mongoose.Schema({
   title: {
       type: String,
       required: true
   },
   body: {
       type: String,
       required: true
   }
   author: {
       type: String,
       required: true
   }
  create_date: {
       type: String,
       required: NULL
   }
})

module.exports = mongoose.model("users",users);
