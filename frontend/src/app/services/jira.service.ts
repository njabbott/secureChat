import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { JiraTicket } from '../models/chat.model';
import { environment } from '../../environments/environment';

export interface CreateTicketRequest {
  summary: string;
  description: string;
  issue_type?: string;
  priority?: string;
}

@Injectable({
  providedIn: 'root'
})
export class JiraService {
  private apiUrl = `${environment.apiUrl}/api/jira`;

  constructor(private http: HttpClient) {}

  createTicket(request: CreateTicketRequest): Observable<JiraTicket> {
    return this.http.post<JiraTicket>(`${this.apiUrl}/create-ticket`, request);
  }
}
