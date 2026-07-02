import React, { createContext, useContext, useState } from 'react';

const ModeContext = createContext({ mode: 'fan', setMode: () => {} });

export function ModeProvider({ children }) {
  const [mode, setMode] = useState(() => localStorage.getItem('f1_mode') || 'fan');
  const update = (nextMode) => {
    setMode(nextMode);
    localStorage.setItem('f1_mode', nextMode);
  };
  return <ModeContext.Provider value={{ mode, setMode: update }}>{children}</ModeContext.Provider>;
}

export const useMode = () => useContext(ModeContext);
