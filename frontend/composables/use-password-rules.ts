export interface PasswordRulesResult {
  minLength: boolean
  hasLetter: boolean
  hasNumber: boolean
  isValid: boolean
}

export function usePasswordRules(password: Ref<string> | ComputedRef<string>) {
  const rules = computed<PasswordRulesResult>(() => {
    const value = password.value ?? ''
    const minLength = value.length >= 8
    const hasLetter = /[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]/.test(value)
    const hasNumber = /\d/.test(value)
    return {
      minLength,
      hasLetter,
      hasNumber,
      isValid: minLength && hasLetter && hasNumber,
    }
  })

  return { rules }
}
