export function parseJwt(token: string) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
          atob(base64).split('').map((c) => {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
          }).join('')
        );
    
        return JSON.parse(jsonPayload);
      } catch (e) {
        return null;
      }
}

export function getTokenFromCookies(tokenName: string) {
    const cookies = document.cookie.split(';');
    const cookie = cookies.find(c => c.trim().startsWith(`${tokenName}=`));
    if (!cookie) return null;
    
    return cookie.split('=')[1];
};
  
export const getUserDataFromToken = () => {
    const accessToken = getTokenFromCookies('accessToken');
    if (!accessToken) return null;
    
    const decodedToken = parseJwt(accessToken);
    if (!decodedToken) return null;
    
    return {
      userId: decodedToken.UserId || decodedToken.sub,
      username: decodedToken.Username,
    };
};