from fastapi import BackgroundTasks
import logging
from typing import Callable, Any, Dict, List
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# 创建线程池执行器
executor = ThreadPoolExecutor(max_workers=4)

class BackgroundTaskManager:
    def __init__(self):
        self.tasks: Dict[str, List[Callable]] = {}
        self._running = False

    async def start(self):
        """启动后台任务管理器"""
        self._running = True
        while self._running:
            for task_name, task_list in self.tasks.items():
                for task in task_list:
                    try:
                        if asyncio.iscoroutinefunction(task):
                            await task()
                        else:
                            # 对于同步函数，在线程池中执行
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(executor, task)
                    except Exception as e:
                        logger.error(f"执行后台任务 {task_name} 失败: {e}")
            await asyncio.sleep(1)  # 避免过度占用 CPU

    def stop(self):
        """停止后台任务管理器"""
        self._running = False

    def add_task(self, task_name: str, task: Callable):
        """添加后台任务"""
        if task_name not in self.tasks:
            self.tasks[task_name] = []
        self.tasks[task_name].append(task)

    def remove_task(self, task_name: str, task: Callable):
        """移除后台任务"""
        if task_name in self.tasks:
            self.tasks[task_name].remove(task)
            if not self.tasks[task_name]:
                del self.tasks[task_name]

# 创建全局后台任务管理器实例
background_tasks = BackgroundTaskManager()

def init_background_tasks():
    """初始化后台任务"""
    try:
        asyncio.create_task(background_tasks.start())
        logger.info("后台任务管理器初始化成功")
    except Exception as e:
        logger.error(f"后台任务管理器初始化失败: {e}")
        raise 