const express = require("express");
const fs = require('fs');
var ejs=require('ejs');
const path = require('path');
const app = express();
const multer  = require('multer');

// const https = require('https');
// const options = {
//   key: fs.readFileSync('key.pem'),
//   cert: fs.readFileSync('cert.pem'),
//   passphrase: '0617'
// };

// https.createServer(options, app).listen(8081, '0.0.0.0', () => {
//   console.log("Application started and Listening on port 8081");
// });

app.listen(3000, () => {
  console.log("Application started and Listening on port 3000");
  console.log("http://localhost:3000 ");
});

// app.listen(8081, '0.0.0.0', () => {
//   console.log("Application started and Listening on port 8081");
// });

// serve your css as static
app.use(express.static(__dirname));

//设置html模板渲染引擎
app.engine('html',ejs.__express);
//设置渲染引擎为html
app.set('view engine','html');


// 修改json接口
app.get("/edit_config", (req, res) => {
    
    var model_path = req.query.model_path;

    var filePath = "./config.json"

    // 读取文件内容
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            res.status(500).send('Error reading file');
        } else {
            
            var data = '{"model_path":"' + model_path + '"}';

            console.log(data);

            // 写入修改后的内容到文件
            fs.writeFile(filePath, data, 'utf8', (err) => {
                if (err) {
                    res.status(500).send('Error writing file');
                } else {
                    
                    res.status(200).send('File updated successfully');
                }
            });
        }
    });
  
});

// 手机端页面
app.get("/muni", (req, res) => {

  var filePath = "./config.json"
  // 同步地遍历目录并返回目录名
  function getSubdirectories(dirPath) {
      return new Promise((resolve, reject) => {
        fs.readdir(dirPath, { withFileTypes: true }, (err, files) => {
          if (err) {
            return reject(err);
          }
    
          // 过滤出目录项
          const directories = files
            .filter(file => file.isDirectory())
            .map(file => file.name);
    
          resolve(directories);
        });
      });
    }

      // 指定目标目录路径
      const targetDir = './models/';

      var dis;

      // 获取目标目录下的所有目录名
      getSubdirectories(targetDir).then((directories) => {
          
          dis = directories;
        })
        .catch((err) => {
          console.error(err);
        });

  // 读取文件内容
  fs.readFile(filePath, 'utf8', (err, data) => {
      if (err) {
          res.status(500).send('Error reading file,配置文件不存在');
      } else {

          console.log(data);

          const jsonData = JSON.parse(data);
          const modelPath = jsonData.model_path;

          dis = JSON.stringify(dis);
          
          res.render(__dirname + "/live2d_m",{model_path: modelPath,model_list:dis});
      }
  });

});

// 大模型 页面操作
app.get("/llm", (req, res) => {

    var filePath = "./config.json"

    // 同步地遍历目录并返回目录名
    function getSubdirectories(dirPath) {
        return new Promise((resolve, reject) => {
          fs.readdir(dirPath, { withFileTypes: true }, (err, files) => {
            if (err) {
              return reject(err);
            }
      
            // 过滤出目录项
            const directories = files
              .filter(file => file.isDirectory())
              .map(file => file.name);
      
            resolve(directories);
          });
        });
      }

        // 指定目标目录路径
        const targetDir = './models/';
        var dis;

        // 获取目标目录下的所有目录名
        getSubdirectories(targetDir).then((directories) => {
            dis = directories;
          })
          .catch((err) => {
            console.error(err);
          });

    // 读取文件内容
    fs.readFile(filePath, 'utf8', (err, data) => {
        if (err) {
            res.status(500).send('Error reading file,配置文件不存在');
        } else {

            console.log(data);

            const jsonData = JSON.parse(data);
            const modelPath = jsonData.model_path;

            dis = JSON.stringify(dis);
            
            res.render(__dirname + "/live2d_llm",{model_path: modelPath,model_list:dis});
        }
    });

});


app.get("/", (req, res) => {
    res.render(__dirname + "/index");
});
