import { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth.jsx';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Car } from 'lucide-react';
import './App.css';

const Login = () => {
  const [intranetId, setIntranetId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login, isAuthenticated } = useAuth();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!intranetId.trim()) {
      setError('Zadejte prosím vaše intranet ID');
      setLoading(false);
      return;
    }

    const result = await login(intranetId.trim());
    
    if (result.success) {
      // Navigation will be handled by the Navigate component above
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
            <Car className="h-6 w-6 text-blue-600" />
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Rezervace firemních vozidel
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Přihlaste se pomocí vašeho intranet ID
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Přihlášení</CardTitle>
            <CardDescription>
              Zadejte vaše intranet ID pro přístup do systému rezervací
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="intranet_id">Intranet ID</Label>
                <Input
                  id="intranet_id"
                  type="text"
                  value={intranetId}
                  onChange={(e) => setIntranetId(e.target.value)}
                  placeholder="Zadejte vaše intranet ID"
                  disabled={loading}
                  className="mt-1"
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button
                type="submit"
                className="w-full"
                disabled={loading}
              >
                {loading ? 'Přihlašování...' : 'Přihlásit se'}
              </Button>
            </form>

            <div className="mt-6 text-sm text-gray-500">
              <p className="font-medium">Demo účty:</p>
              <ul className="mt-2 space-y-1">
                <li>• <code className="bg-gray-100 px-1 rounded">admin</code> - Administrátor vozového parku</li>
                <li>• <code className="bg-gray-100 px-1 rounded">employee</code> - Běžný zaměstnanec</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Login;

