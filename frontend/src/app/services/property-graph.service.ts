import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {map, Observable} from 'rxjs';
import {PropertyGraphRelation} from "../dtos/property_graph_relation";

@Injectable({
  providedIn: 'root'
})
export class PropertyGraphService {
  // TODO: Add other endpoints / make endpoint dynamic
  private apiUrl = 'http://127.0.0.1:8000';
  private cypherUrl = `${this.apiUrl}/cypher`;
  private redisUrl = `${this.apiUrl}/queries`;

  constructor(
    private http: HttpClient
  ) { }

  runCypherQuery(query: string): Observable<any> {
    return this.http.post<any>(this.cypherUrl, { query });
  }

  getPastQueries(): Observable<any> {
    return this.http.get<any>(this.redisUrl);
  }
}
