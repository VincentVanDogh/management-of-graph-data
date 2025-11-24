import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { Neo4jPropertyGraphComponent } from './neo4j-property-graph/neo4j-property-graph.component';
import { CustomPropertyGraphComponent } from './custom-property-graph/custom-property-graph.component';
import { HeaderComponent } from './header/header.component';
import { RdfComponent } from './rdf/rdf/rdf.component';

@NgModule({
  declarations: [
    AppComponent,
    Neo4jPropertyGraphComponent,
    CustomPropertyGraphComponent,
    HeaderComponent,
    RdfComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
