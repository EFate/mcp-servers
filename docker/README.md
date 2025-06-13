# FastAPI MCP 服务器 Docker 部署指南  


## 📁 项目结构概览  
核心文件组织如下：  

```bash
.
├── app/                  # 应用源代码（含模块化服务接口）
├── docker/
│   ├── Dockerfile        # 镜像构建定义（基于 Python 3.10）
│   ├── docker-compose.yml # 服务编排配置（多容器协调部署）
│   └── start.sh          # 容器启动脚本（含环境初始化）
├── .dockerignore         # 构建时忽略文件（如虚拟环境、缓存）
├── pyproject.toml        # 项目依赖管理（Poetry 配置）
└── run.py                # 应用启动入口（FastAPI 实例初始化）
```


## 🚀 部署说明  


### 🅰️ 方式一：Docker Compose 编排部署（推荐）  
通过编排文件一键完成构建、启动与服务关联，适合生产环境。  


#### 1. 进入部署目录  
```bash
cd docker  # 确保在含 docker-compose.yml 的目录执行
```


#### 2. 构建并启动服务  
```bash
docker-compose up --build -d
```
- `--build`：强制重新构建镜像（首次部署或依赖变更时使用）  
- `-d`：后台运行容器（分离模式）  


#### 3. 服务验证  
访问 `http://localhost:13000` 查看根路径响应，或通过 Swagger 文档：  
`http://localhost:13000/docs`  


#### 4. 停止服务  
```bash
docker-compose down  # 停止并移除容器、网络
```


### 🅱️ 方式二：Docker CLI 手动部署  
适合理解部署流程或调试场景，需在项目根目录执行。  


#### 1. 构建镜像  
```bash
docker build -t mcp-server:latest -f docker/Dockerfile .
```
- `-t`：指定镜像名称与标签（`名称:版本`）  
- `-f`：指定 Dockerfile 路径  
- `.`：当前目录作为构建上下文  


#### 2. 启动容器  
```bash
docker run -d \
  -p 13000:13000 \
  --name mcp-container \
  --restart unless-stopped \
  mcp-server:latest
```
- `-p`：端口映射（主机端口:容器端口）  
- `--restart`：容器重启策略（非手动停止时自动重启）  


#### 3. 查看日志  
```bash
docker logs mcp-container -f  # -f 持续跟踪日志
```


#### 4. 停止与移除容器  
```bash
docker stop mcp-container  # 停止容器
docker rm mcp-container    # 移除容器
```
