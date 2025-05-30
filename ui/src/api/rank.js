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
export function getAvatar() {
  return request({
    url: '/avatar',
    method: 'get'
  })
}

export function getUsername() {
  return request({
    url: '/username',
    method: 'get'
  })
}

export function postFeedback(data) {
  return request({
    url: '/feedback',
    method: 'post',
    data
  })
}

export function getCards() {
  return request({
    url: '/get_cards',
    method: 'get'
  })
}

export function getMusic() {
  return request({
    url: '/music',
    method: 'get'
  })
}

export function getAiSummarizes(){
  return request({
    url: '/todayTopNews',
    method: 'get'
  })
}

export function refresh(){
  return request({
    url: '/refresh',
    method: 'get'
  })
}

export function getHolidays(){
  return request({
    url: '/holiday',
    method: 'get'
  })
}

export function subscribe(data) {
  return request({
    url: '/subscribe',
    method: 'post',
    data
  })
}
export function unsubscribe(data) {
  return request({
    url: '/unsubscribe',
    method: 'post',
    data
  })
}