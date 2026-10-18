import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

const fullscreenSlice = createSlice({
  name: 'fullscreen',
  initialState: { active: false },
  reducers: {
    fullscreenChanged(state, action: PayloadAction<boolean>) {
      state.active = action.payload
    },
  },
})

export const { fullscreenChanged } = fullscreenSlice.actions
export default fullscreenSlice.reducer
