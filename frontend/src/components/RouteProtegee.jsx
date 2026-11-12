import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useMoi } from '../hooks/useAuth';

export default function RouteProtegee() {
  const moi = useMoi();
  const location = useLocation();

  if (moi.isLoading) return <p style={{ padding: '2rem' }}>Chargement…</p>;

  if (moi.isError || !moi.data) {
    // On garde la page visée pour y revenir après connexion.
    return <Navigate to="/connexion" state={{ depuis: location }} replace />;
  }

  return <Outlet />;
}