import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

const keepAwakeSlice = createSlice({
  name: 'keepAwake',
  initialState: { active: false },
  reducers: {
    keepAwakeChanged(state, action: PayloadAction<boolean>) {
      state.active = action.payload
    },
  },
})

export const { keepAwakeChanged } = keepAwakeSlice.actions
export default keepAwakeSlice.reducer
