利用Agent控制键鼠实现自动办公的AI Agent。

服务端有一个规划模块，一个反思模块，一个执行模块
规划下面是反思，与token统计模块
执行与规划之间是指令解析模块
客户端只有执行与显示规划。

---

- [ ] 规划模块
  - [X] 计算token数（5行）
  - [ ] 对话系统
    - [X] 用户与agent对话（记录对话历史15行）
    - [ ] 主从agent间对话（服务器端内部对话，在客户端显示出来，10行）
    - [ ] 从agent搜索（生成搜索引擎搜索词，搜索引擎返回从agent提示词10行）
    - [ ] 对话（输入提示词，返回回答10行）
    - [ ] 请求ChatGPT（10行）
  - [ ] 反思模块
    - [ ] 历史的读取
      - [ ] 动作（5行）
      - [ ] 反馈（5行）
    - [ ] 主agent反思（10行）
    - [ ] 从agent反思（10行）
- [X] 执行模块
- [ ] 提示词版本控制
  - [ ] 统计修改部分
    - [ ] 增加（5行）
    - [ ] 更改（5行）
    - [ ] 删除（5行）
  - [ ] 新版本发布
    - [ ] 自动补充更新词（增加了什么文件，更改了什么文件，删除了什么文件10行）
    - [ ] 录入数据库（agent名，内容，增删改部分10行）
    - [ ] 录入搜索引擎elasticsearch（agent名，内容10行）
  - [ ] 合并（10行）
  - [ ] 分叉
    - [ ] 自分叉（20行）
    - [ ] 其他用户分叉（20行）
- [ ] 键鼠控制提示词编写模块
  - [ ] 显示别人的提示词（前端30行，后端20行）
    - [ ] 搜索提示词（前端10行，后端10行）
    - [ ] 显示提示词（前端20行，后端10行）
  - [X] 编写自己的提示词
    - [X] 编写（前端5行，后端5行）
    - [X] 记录入数据库（后端5行）
    - [X] 记录入搜索引擎elasticsearch（后端5行）
  - [ ] 从agent分叉（复制到自己的工作区下10行）
- [ ] 付费模块
  - [ ] 从agent计算贡献度（按字数10行）
  - [ ] agent费用分发（100行）
  - [ ] 充值（100行）
    - [ ] 生成序列号（生成一个字母数字串并保存）
    - [ ] 序列号读取（查找并返回序列号是否存在）
- [ ] 用户系统
  - [X] 注册（100行）
  - [X] 登录（100行）
