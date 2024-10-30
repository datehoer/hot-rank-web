const localStorageUtils = {
    // 获取指定 key 的值
    get(key, defaultValue = null) {
      const value = localStorage.getItem(key);
      return value ? JSON.parse(value) : defaultValue;
    },
  
    // 设置指定 key 的值
    set(key, value) {
      localStorage.setItem(key, JSON.stringify(value));
    },
  
    // 删除指定 key 的值
    remove(key) {
      localStorage.removeItem(key);
    },
  };
  
  export default localStorageUtils;