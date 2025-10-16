// Utility functions for route handling

export const isPatientRoute = (pathname = window.location.pathname) => {
  return pathname.startsWith('/patient/')
}

export const isStaffRoute = (pathname = window.location.pathname) => {
  return pathname.startsWith('/staff/')
}

export const shouldRequireAuth = (pathname = window.location.pathname) => {
  return isStaffRoute(pathname) && !pathname.includes('/staff/login')
}
