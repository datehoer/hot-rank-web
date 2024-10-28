import request from '@/utils/request'

export function getRankList() {
  return request({
    url: '/rank/hot',
    method: 'get'
  })
}

export function getCopyWriting() {
  return request({
    url: '/rankCopyWriting',
    method: 'get'
  })
}

export function getYellowCalendar() {
  return request({
    url: '/yellowCalendar',
    method: 'get'
  })
}