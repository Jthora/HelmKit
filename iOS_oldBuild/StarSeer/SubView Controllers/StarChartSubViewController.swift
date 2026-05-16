//
//  AstrologicalCoreSubViewController.swift
//  HelmKit
//
//  Created by Jordan Trana on 6/5/19.
//  Copyright © 2019 Jordan Trana. All rights reserved.
//

import UIKit
import SpriteKit

class StarChartSubViewController: SubViewController {
    
    var scene:SKScene?
    var spriteKitView:SKView
    
    init(wideNarrowContainerView:UIView, wideNarrowSpriteKitView:SKView) {
        
        self.spriteKitView = wideNarrowSpriteKitView
        
        super.init(view: wideNarrowContainerView)
        
        self.scene = SKScene(size: view.bounds.size)
        
        setup()
    }
    
    func setup() {
        setupScene()
    }
    
    func setupScene() {
        spriteKitView.presentScene(scene)
        let circle:SKShapeNode = SKShapeNode(circleOfRadius: view.bounds.size.width/2)
        circle.position = CGPoint(x: view.bounds.size.width/2, y: view.bounds.size.height/2)
        circle.name = "initialDisk"
        circle.strokeColor = SKColor.gray
        circle.glowWidth = 10.0
        circle.fillColor = SKColor.white
        spriteKitView.scene?.addChild(circle)
    }
}
