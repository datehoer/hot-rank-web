import request from '@/utils/request'

export function getRankList() {
    return request({
      url: '/rank/hot',
      method: 'get'
    })
  }