import { createSlice } from "@reduxjs/toolkit";

interface UIState {
    expand: boolean;
}
  
const initialState: UIState = {
    expand: true
}

export const uiSlice = createSlice({
    name: 'ui',
    initialState,
    reducers: {
      toggleExpand: (state) => {
        state.expand = !state.expand;
      },
      setExpand: (state, action) => {
        state.expand = action.payload;
      }
    }
});

export const { toggleExpand, setExpand } = uiSlice.actions
export default uiSlice.reducer
export const selectExpandState = (state: { ui: { expand: boolean }}) => state.ui.expand

