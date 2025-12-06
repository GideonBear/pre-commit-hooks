#!/bin/bash

# Bad:
function myfun {
function myfun() {
myfun {
myfun () {
myfun(){

# Good:
myfun() {
