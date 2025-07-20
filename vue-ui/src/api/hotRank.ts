import { get } from '@/utils/request'

// 定义接口返回的数据类型
export interface HotItem {
  hot_label: string
  hot_url: string
  hot_value: number
}

export interface HotSection {
  name: string
  insert_time?: string
  data: HotItem[]
}

export interface HotRankResponse {
  code: number
  msg: string
  data: HotSection[]
}

// 黄历数据类型定义
export interface YellowCalendarData {
  gregorian_calendar: string
  lunar_calendar: string
  good_actions: string[]
  bad_actions: string[]
}

export interface YellowCalendarResponse {
  code: number
  msg: string
  data: YellowCalendarData
}

export interface MusicData {
  id: number
  title: string
  url: string
  cover: string
}

export interface MusicResponse {
  code: number
  msg: string
  data: MusicData[]
}

// 获取热门排行榜数据
export const getHotRank = (): Promise<HotRankResponse> => {
  return get<HotRankResponse>('/rank/hot')
}

// 获取黄历数据
export const getYellowCalendar = (): Promise<YellowCalendarResponse> => {
  return get<YellowCalendarResponse>('/yellowCalendar')
}

// 获取音乐数据
export const getMusic = (): Promise<MusicResponse> => {
  return get<MusicResponse>('/music')
}
