原作者：[奋奋狮子](http://tieba.baidu.com/home/main?un=%E5%A5%8B%E5%A5%8B%E7%8B%AE%E5%AD%90)

因 Py2exe 年久失修，Nuitka 兼容性欠佳，建议打包环境改为 PyInstaller:

`pyinstaller -F *.py`

暂不支持在 64 位 Python 环境下打包出 `Zen.dll` 需要的 32 位程序。

统一修改：

- 兼容 Python3；
- 使用 `pipenv` 管理依赖；
- 使用 `black` 工具格式化；注：如遇到 `pipenv` 因 `black` 无法 `lock` 的问题，可尝试 `pipenv lock --pre`
- 将 `log` 文件名规范格式化为 `.\logs\年月日-时分秒.log`；
- 增加注释；
- 刷版本号。

`Zen7GTP` 修改：

- 修改默认参数：关闭控制台；首位计算量 10k.

`Zen6GTP` 修改：

- 规范应用名；
- 移除 `multiprocessing` 模块依赖。