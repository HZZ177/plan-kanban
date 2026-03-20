export class ReconnectManager {
  private attempts = 0

  nextDelay(base = 1000): number {
    this.attempts += 1
    return Math.min(base * this.attempts, 10000)
  }

  reset(): void {
    this.attempts = 0
  }
}
