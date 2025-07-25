import { Link, useNavigate } from 'react-router-dom'
import { MapPin, User, LogOut, Settings } from 'lucide-react'
import { Button } from './ui/button'
import { useAuth } from '../contexts/AuthContext'
import logoTudoMais from '../assets/logoTudoMais.png'

const Header = () => {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <header className="bg-tudo-mais-green shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <img 
              src={logoTudoMais} 
              alt="Tudo Mais" 
              className="h-10 w-auto"
            />
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-4">
            {user ? (
              <>
                {isAdmin() && (
                  <Button
                    variant="ghost"
                    className="tudo-mais-white hover:bg-white/20"
                    onClick={() => navigate('/admin')}
                  >
                    <Settings className="w-4 h-4 mr-2" />
                    Painel Admin
                  </Button>
                )}
                
                <Button
                  variant="ghost"
                  className="tudo-mais-white hover:bg-white/20"
                  onClick={handleLogout}
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sair
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  className="tudo-mais-white hover:bg-white/20"
                  onClick={() => navigate('/login')}
                >
                  <User className="w-4 h-4 mr-2" />
                  Entrar
                </Button>
                
                <Button
                  variant="outline"
                  className="border-white text-white hover:bg-white hover:text-green-600"
                  onClick={() => navigate('/register')}
                >
                  Anunciar
                </Button>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header

