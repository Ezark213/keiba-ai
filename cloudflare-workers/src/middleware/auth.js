/**
 * 認証ミドルウェア
 */

export async function authMiddleware(request, env) {
  const auth = request.headers.get('Authorization');
  
  if (!auth || !auth.startsWith('Bearer ')) {
    return {
      error: true,
      response: new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      })
    };
  }
  
  const token = auth.substring(7);
  
  if (token !== env.SYNC_TOKEN) {
    return {
      error: true,
      response: new Response(JSON.stringify({ error: 'Invalid token' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      })
    };
  }
  
  return { error: false };
}