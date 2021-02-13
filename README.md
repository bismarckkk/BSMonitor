# BSMonitor
这是一个为单片机开发准备的调试工具  
用于图形化监视变量和其他调试功能

## 支持
目前已经完成使用pyocd的轮询模式后端，兼容STlink, DAPlink, Jlink等常见调试器

## 使用
在使用前应该安装python3.8或以上版本，并在安装时选择将安装路径加入PATH  
然后执行以下命令  
若相关依赖安装缓慢请换用国内镜像源
```shell
git clone https://github.com/abc55660745/BSMonitor.git
cd BSMonitor
pip install -r requirements.txt
python app.py
```

## TODO
+ 加入pyocd中断模式后端
+ 完善后端插件仓库
+ 进一步优化动画显示效果

## 为此项目贡献代码
现急需开发其他兼容后端，例如兼容匿名协议，使用GDB等  
  
后端使用插件式开发，可以参考`plugins/random.py`，这是一个极简单的例子，实现了一个后端所需要的所有功能  
后端需要继承`base.py`中的Base类，以及需要在`templates/methods`中加入与插件同名的html文件，该文件应当使用jinja2模板
继承`templates/edit.html`，可以参考`templates/methods/random.html`，实现所后端所需要参数的输入，所有参数会以字典形式
在子类`init()`函数调用前写入`self.config`，可从中调用  
  
同时欢迎提其他PR