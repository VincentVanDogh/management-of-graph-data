import {Injectable} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class Globals {
  readonly backendUri: string = this.findBackendUrl();

  private findBackendUrl(): string {
    if (window.location.port === '4200') {
      return 'http://127.0.0.1:8000';
    } else {
      return window.location.protocol + '//' + window.location.host + window.location.pathname + 'api/v1';
    }
  }
}


