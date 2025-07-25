import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      // Decodificar o token JWT para obter informações do usuário
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        setUser({
          id: payload.user_id,
          type: payload.user_type
        })
      } catch (error) {
        console.error('Token inválido:', error)
        logout()
      }
    }
    setLoading(false)
  }, [token])

  const login = (token) => {
    localStorage.setItem('token', token)
    setToken(token)
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      setUser({
        id: payload.user_id,
        type: payload.user_type
      })
    } catch (error) {
      console.error('Erro ao decodificar token:', error)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  const isAdmin = () => {
    return user?.type === 'admin'
  }

  const isAdvertiser = () => {
    return user?.type === 'advertiser'
  }

  const isConsumer = () => {
    return user?.type === 'consumer'
  }

  const value = {
    user,
    token,
    login,
    logout,
    isAdmin,
    isAdvertiser,
    isConsumer,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

